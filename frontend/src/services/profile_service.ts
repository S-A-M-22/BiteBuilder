import apiClient from "@/lib/apiClient"
// --------------------------------------------------------
// Types
// --------------------------------------------------------
export type GenderType = "male" | "female" | "other";
export type Profile = {
  id: string;
  username: string | null;
  email: string;
  age: number | null;
  gender: GenderType | null;
  height_cm: number | null;
  weight_kg: number | null;
  postcode: string | null;
  avatar?: string | null;
};

export const profileService = {

  async fetchProfile(): Promise<Profile>{
    const res = await apiClient.get("/auth/fetch_profile/", { withCredentials: true })

    return res.data as Profile;
  },

  /** Save partial updates to the profile */
  async updateProfile(patch: Partial<Profile>): Promise<Profile> {
    const res = await apiClient.post("/auth/update_profile/", patch);
    return res.data as Profile
  },






























}
